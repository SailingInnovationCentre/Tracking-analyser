-- Source for calculations: https://en.wikipedia.org/wiki/Rotation_of_axes
-- Basic idea: rotate the startline to a vertical line, and use the same rotation on the boats' coordinates. 
-- The y coordinate is then the relative start position (between 0 and 1). 

--IF OBJECT_ID(N'powertracks.FindOrthPosOnLine', N'FN') IS NOT NULL 
--    DROP FUNCTION powertracks.FindOrthPosOnLine ;
--GO

-- Use float instead of decimals, in order to prevent underfloat (and divide by zeroes). 
CREATE FUNCTION powertracks.FindOrthPosOnLine(@l1x float, @l1y float, @l2x float, @l2y float, @px float, @py float)
  RETURNS DECIMAL(9,3)
  AS
  BEGIN
    DECLARE @r as float; 
    DECLARE @theta as float; 
    DECLARE @translated_px as float; 
    DECLARE @translated_py as float; 
    DECLARE @rotated_py AS DECIMAL(9,5); 

    SET @r = sqrt( power(@l2x-@l1x, 2) + power(@l2y-@l1y, 2) );
    SET @theta = -atan( (@l2x - @l1x) / ( @l2y - @l1y) );

    SET @translated_px = @px - @l1x; 
    SET @translated_py = @py - @l1y; 

    SET @rotated_py = (-@translated_px * sin(@theta) + @translated_py * cos(@theta)) / @r; 

    IF @l2y < @l1y
      SET @rotated_py= - @rotated_py;
    
    RETURN 1 - @rotated_py; 
    
  END;